// REPO: bolt.new | FILE: app/lib/stores/chat.ts | CONSTELLATION25

import { map } from 'nanostores';

export const chatStore = map({
  started: false,
  aborted: false,
  showChat: true,
});
