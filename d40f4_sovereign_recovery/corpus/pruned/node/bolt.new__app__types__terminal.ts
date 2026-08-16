// REPO: bolt.new | FILE: app/types/terminal.ts | CONSTELLATION25

export interface ITerminal {
  readonly cols?: number;
  readonly rows?: number;

  reset: () => void;
  write: (data: string) => void;
  onData: (cb: (data: string) => void) => void;
}
