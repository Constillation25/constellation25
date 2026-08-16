// REPO: bolt.new | FILE: app/lib/persistence/ChatDescription.client.tsx | CONSTELLATION25

import { useStore } from '@nanostores/react';
import { description } from './useChatHistory';

export function ChatDescription() {
  return useStore(description);
}
