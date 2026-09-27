import { MicroclimateCard } from "./card";
import { MicroclimateEditor } from "./editor";
class ChannelCard extends MicroclimateCard {}
class ControllerCard extends MicroclimateCard {}
if (!customElements.get("microclimate-channel-card"))
  customElements.define("microclimate-channel-card", ChannelCard);
if (!customElements.get("microclimate-controller-card"))
  customElements.define("microclimate-controller-card", ControllerCard);
if (!customElements.get("microclimate-card-editor"))
  customElements.define("microclimate-card-editor", MicroclimateEditor);

type PickerCard = { type: string; name: string; description: string };
const registry = window as unknown as { customCards?: PickerCard[] };
const picker = Array.isArray(registry.customCards) ? registry.customCards : [];
for (const card of [
  {
    type: "microclimate-channel-card",
    name: "Microclimate channel",
    description:
      "Daily, Multi and seasonal schedule with explicit Save/Cancel.",
  },
  {
    type: "microclimate-controller-card",
    name: "Microclimate controller",
    description: "Shared season start dates.",
  },
]) {
  if (!picker.some((existing) => existing?.type === card.type)) picker.push(card);
}
registry.customCards = picker;
