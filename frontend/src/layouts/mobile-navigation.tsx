import * as Dialog from "@radix-ui/react-dialog";
import { Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Navigation } from "@/layouts/navigation";
import { useUiStore } from "@/stores/ui-store";

export function MobileNavigation() {
  const open = useUiStore((state) => state.mobileNavigationOpen);
  const setOpen = useUiStore((state) => state.setMobileNavigationOpen);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[#101828]/45 backdrop-blur-[2px] lg:hidden" />
        <Dialog.Content className="fixed inset-y-0 left-0 z-50 flex w-[min(84vw,320px)] flex-col border-r bg-[#fbfcfc] p-4 shadow-2xl outline-none lg:hidden">
          <Dialog.Title className="sr-only">主导航</Dialog.Title>
          <div className="flex h-14 items-center justify-between px-2">
            <div className="flex items-center gap-3">
              <span className="grid size-9 place-items-center rounded-xl bg-primary text-white">
                <Sparkles className="size-[18px]" aria-hidden="true" />
              </span>
              <span className="font-semibold">OmniSage</span>
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="icon" aria-label="关闭导航">
                <X className="size-5" aria-hidden="true" />
              </Button>
            </Dialog.Close>
          </div>
          <div className="mt-5 flex-1">
            <Navigation onNavigate={() => setOpen(false)} />
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
