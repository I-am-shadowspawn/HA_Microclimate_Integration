import { it, expect } from "vitest";
import { newId } from "../src/id";
it("produces distinct valid UUID v4 request IDs", () => {
  const ids = Array.from({ length: 100 }, () => newId());
  expect(new Set(ids).size).toBe(100);
  for (const id of ids)
    expect(id).toMatch(
      /^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/,
    );
});
