import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { boundPath, filePath, guardRuntimePaths } from '../src/paths.js';

const roots: string[] = [];
function fixture(): string {
  const root = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'nullius-native-path-')));
  roots.push(root);
  return root;
}
afterEach(() => {
  for (const root of roots.splice(0)) fs.rmSync(root, {recursive:true, force:true});
});

describe.runIf(process.platform === 'win32')('native project paths', () => {
  it('rejects Win32 aliases while accepting native absolute metadata paths', () => {
    const root = fixture();
    expect(() => boundPath(root, 'inputs\\escape')).toThrow('Unsafe project path');
    for (const value of ['AGENTS.md.', 'AGENTS.md ', 'inputs/note:secret', 'inputs/CON.txt', `${root}\\inputs\\..\\escape`]) {
      expect(() => filePath(root, value, true), value).toThrow('Unsafe project path');
    }
    const input = path.join(root, 'inputs', '\u65b9\u7814.txt');
    expect(filePath(root, input, true)).toBe(input);
  });

  it('checks referenced historical evidence using native directory access', () => {
    const root = fixture();
    const outside = fixture();
    fs.mkdirSync(path.join(root, '.nullius'));
    fs.mkdirSync(path.join(root, 'team/runs/past/data'), {recursive:true});
    fs.symlinkSync(outside, path.join(root, 'team/runs/past/data/external'), 'junction');
    fs.writeFileSync(path.join(root, '.nullius/state.json'), JSON.stringify({
      run_id:'past', artifacts:{x:'orch://runs/past/artifact/data/external/value.json'},
    }));
    expect(() => guardRuntimePaths(root)).toThrow('Symlinks are not accepted');
    expect(fs.readdirSync(outside)).toEqual([]);
  });
});
