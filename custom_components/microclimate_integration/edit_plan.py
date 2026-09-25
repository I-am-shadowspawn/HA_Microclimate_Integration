"""Pure whole-draft validation and deterministic, frozen-source pin ordering."""
from dataclasses import dataclass
from itertools import permutations
from .card_model import input_value, value_of
from .write_contract import (definition_for, write_definitions, applicable, serialize, matches,
                             validate_input, timing_mode, WriteValidationError)


@dataclass(frozen=True)
class Step:
    field: object
    value: object
    wire: str


@dataclass
class EditPlan:
    steps: list[Step]
    expected: dict
    fields: list


def require(condition, code='invalid_patch'):
    if not condition:
        raise WriteValidationError(code)


def build_plan(model, channel, data, patch):
    require(type(patch) is dict and patch.get('kind') in ('mode', 'channel', 'season_dates'))
    kind = patch['kind']
    changes = patch.get('fields', {})
    require(type(changes) is dict and len(changes) <= 24)
    desired = dict(changes)
    require(set(patch) <= {'kind', 'fields', 'schedule'})
    require('schedule' not in patch or kind == 'channel')
    require((channel is None) == (kind == 'season_dates'))
    order = list(desired)
    schedule = patch.get('schedule')
    if schedule is not None:
        require(type(schedule) is dict and set(schedule) == {'mode', 'points'})
        points = schedule['points']
        require(type(points) is list and 2 <= len(points) <= 8)
        mode_field = definition_for(model, f'{channel}_period_1_time')
        mode = timing_mode(mode_field, data)
        require(schedule['mode'] == mode and mode in ('Day Night', 'Seasonal', 'Multi'), 'stale_context')
        require(mode == 'Multi' or len(points) == (2 if mode == 'Day Night' else 8))
        for point in points:
            require(type(point) is dict and set(point) <= {'seconds', 'target_native', 'draft_id', 'source_slot'}
                    and {'seconds', 'target_native'} <= set(point))
            require(type(point['seconds']) is int and 0 <= point['seconds'] < 86400)
            require(type(point['target_native']) in (int, float))
        clocks = [p['seconds'] for p in points]
        if mode == 'Multi':
            require(clocks == sorted(set(clocks)), 'invalid_point_order')
            require(all(p['seconds'] != 0 or p['target_native'] != 0 for p in points), 'reserved_empty_point')
        else:
            require(all(clocks[i] != clocks[i+1] for i in range(0, len(points), 2)), 'duplicate_boundary')
        slots = list(range(1, len(points)+1))
        if mode == 'Multi':
            old = [(value_of(definition_for(model, f'{channel}_period_{i}_time'), data),
                    value_of(definition_for(model, f'{channel}_period_{i}_setpoint'), data)) for i in range(1, 9)]
            while old and old[-1] == (0, 0):
                old.pop()
            new = [(p['seconds'], p['target_native']) for p in points]
            # Only exact retained pairs qualify for a single structural shift.
            if len(new) == len(old)+1:
                for k in range(len(new)):
                    if new[:k]+new[k+1:] == old:
                        slots = list(range(len(new), k+1, -1)) + [k+1]
                        break
            elif len(new) == len(old)-1:
                for k in range(len(old)):
                    if old[:k]+old[k+1:] == new:
                        slots = list(range(k+1, len(new)+1))
                        break
            # Include unchanged prefix for full validation, but place no-op steps last.
            slots += [i for i in range(1, len(points)+1) if i not in slots]
            slots += list(range(8, len(points), -1))
        templates = set()
        for i in slots:
            clear = i > len(points)
            p = {'seconds': 0, 'target_native': 0} if clear else points[i-1]
            keys = [(f'{channel}_period_{i}_time', p['seconds']),
                    (f'{channel}_period_{i}_setpoint', p['target_native'])]
            if not clear:
                keys.reverse()
            for key, value in keys:
                require(key not in desired)
                desired[key] = value
                order.append(key)
                f = definition_for(model, key)
                if f.kind == 'time':
                    encoded = serialize(f, input_value(f, value), data)
                    templates.add(tuple(encoded.split('\0')[2:]))
        require(len(templates) <= 1, 'incompatible_time_templates')
    require(bool(desired))
    fields = [definition_for(model, key) for key in desired]
    for f in fields:
        require(f.channel == channel)
        require(applicable(f, data), 'unsupported_capability')
        validate_input(f, input_value(f, desired[f.key]))
        if kind == 'mode':
            require(len(fields) == 1 and f.kind == 'enum')
        elif kind == 'channel':
            require(f.kind != 'enum')
            require(f.index is None or schedule is not None)
        else:
            require(f.kind == 'date')
    if kind == 'season_dates':
        # Find a valid path without scratch dates or intermediate invalid calendars.
        for candidate in permutations(order):
            working = dict(data)
            try:
                for key in candidate:
                    f = definition_for(model, key)
                    working[f.pin] = serialize(f, desired[key], working)
            except WriteValidationError:
                continue
            order = list(candidate)
            break
        else:
            raise WriteValidationError('no_valid_date_path')
    working = dict(data)
    steps = []
    for key in order:
        f = definition_for(model, key)
        value = input_value(f, desired[key])
        wire = serialize(f, value, working)
        if not matches(f, wire, working):
            steps.append(Step(f, value, wire))
        working[f.pin] = wire
    return EditPlan(steps, working, fields)
