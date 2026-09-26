import { en } from "./locales/en";
export type MessageKey = keyof typeof en;
export type Catalogue = Partial<Record<MessageKey, string>>;
export function message(key: MessageKey, params: Record<string, string | number> = {}, catalogue: Catalogue = en): string {
  return (catalogue[key] ?? en[key]).replace(/\{(\w+)\}/g, (_, name: string) => String(params[name] ?? `{${name}}`));
}
export function localize(key: MessageKey, language?: string, params: Record<string, string | number> = {}, catalogues: Record<string, Catalogue> = {}): string {
  return message(key, params, catalogues[language ?? ""] ?? catalogues[language?.split("-")[0] ?? ""] ?? en);
}
