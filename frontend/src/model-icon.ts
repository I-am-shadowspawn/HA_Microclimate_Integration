const ICONS: Record<string, string> = {
  "Evo Connect": "evo-connect.png",
  "Evo Connect 2": "evo-connect-ii.png",
  "Evo Connect 3": "evo-connect-iii.png",
};

export function modelIconUrl(model: string): string | null {
  const file = ICONS[model];
  return file ? `/microclimate_integration/${file}` : null;
}
