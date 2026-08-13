import { screen } from "@testing-library/react";
import { describe,expect,it,vi } from "vitest";
import { getModels } from "@/api/system";
import { PreferencesForm } from "@/features/settings/preferences-form";
import { renderWithProviders } from "@/test/render";
vi.mock("@/api/system",()=>({getModels:vi.fn()}));
describe("PreferencesForm",()=>{it("lists scoped model keys",async()=>{vi.mocked(getModels).mockResolvedValue([{key:"ollama::local::qwen",connection_id:"local",provider:"ollama",id:"qwen",display_name:"Qwen",source:"local_runtime",available:true,task_types:["chat"],input_modalities:["text"],output_modalities:["text"],capabilities:{reasoning_efforts:[]},stale:false,vision:false}]);renderWithProviders(<PreferencesForm/>);expect(await screen.findByRole("option",{name:"ollama · Qwen"})).toHaveValue("ollama::local::qwen");});});
