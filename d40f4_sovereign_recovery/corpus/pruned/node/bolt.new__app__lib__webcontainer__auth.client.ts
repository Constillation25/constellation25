// REPO: bolt.new | FILE: app/lib/webcontainer/auth.client.ts | CONSTELLATION25

/**
 * This client-only module that contains everything related to auth and is used
 * to avoid importing `@webcontainer/api` in the server bundle.
 */

export { auth, type AuthAPI } from '@webcontainer/api';
