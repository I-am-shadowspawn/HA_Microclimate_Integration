import { MicroclimateCard } from "./card";
import { MicroclimateEditor } from "./editor";
class ChannelCard extends MicroclimateCard {}
class ControllerCard extends MicroclimateCard {}
customElements.define("microclimate-channel-card", ChannelCard);
customElements.define("microclimate-controller-card", ControllerCard);
customElements.define("microclimate-card-editor", MicroclimateEditor);
const registry = window as unknown as { customCards: unknown[] };
registry.customCards = registry.customCards ?? [];
registry.customCards.push(
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
);
