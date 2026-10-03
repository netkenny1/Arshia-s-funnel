declare module "virtual:arshia" {
  import type { Artist, Event } from "../plugins/arshia-data";
  const data: { artist: Artist; upcoming: Event[]; base: string; built: string };
  export default data;
}
