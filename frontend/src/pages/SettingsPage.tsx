import { PageHeading } from "@/components/common/page-heading";
import { ProviderConnections } from "@/features/settings/provider-connections";
import { PreferencesForm } from "@/features/settings/preferences-form";
import { WikiSettings } from "@/features/settings/wiki-settings";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeading
        eyebrow="Preferences"
        title="设置"
        description="管理对话默认值、Wiki 服务模式和在线模型密钥。"
      />
      <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <div className="min-w-0 space-y-5">
          <PreferencesForm />
          <WikiSettings />
        </div>
        <div className="min-w-0">
          <ProviderConnections />
        </div>
      </div>
    </div>
  );
}
