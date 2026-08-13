import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { getModels } from "@/api/system";
import { queryKeys } from "@/api/query-keys";
import { Button } from "@/components/ui/button";
import { usePreferencesStore } from "@/stores/preferences-store";

export function PreferencesForm() {
  const preferences = usePreferencesStore();
  const [modelKey,setModelKey]=useState(preferences.defaultModelKey);
  const models=useQuery({queryKey:queryKeys.system.chatModels,queryFn:({signal})=>getModels(signal,{chatOnly:true})});
  return <section className="rounded-2xl border bg-surface"><div className="border-b px-5 py-4"><h2 className="font-semibold">对话默认值</h2><p className="mt-1 text-xs text-muted">仅保存连接范围模型 key，不保存凭证。</p></div><div className="space-y-4 p-5"><select aria-label="默认模型" className="h-11 w-full rounded-xl border px-3" value={modelKey} onChange={(e)=>setModelKey(e.target.value)}><option value="">不预选模型</option>{models.data?.map(model=><option key={model.key} value={model.key}>{model.provider} · {model.display_name}</option>)}</select>{models.isError&&<p className="text-xs text-danger">模型目录读取失败，当前编辑值未被覆盖。</p>}<Button onClick={()=>preferences.setPreferences({defaultModelKey:modelKey,ragEnabled:preferences.ragEnabled,wikiEnabled:preferences.wikiEnabled})}>保存默认设置</Button></div></section>;
}
