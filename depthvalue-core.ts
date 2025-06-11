export interface DepthDecomposition {
  baseValue: number;
  precisionFactor: number;
  components: number[];
}

export function primeFactorize(n: number): number[] {
  const factors: number[] = [];
  let d = 2;
  while (n > 1) {
    while (n % d === 0) {
      factors.push(d);
      n /= d;
    }
    d++;
    if (d * d > n && n > 1) {
      factors.push(n);
      break;
    }
  }
  return factors;
}

export function computeDepthValue(value: number, base: number = 1e5): DepthDecomposition {
  const scaled = Math.round(value * base);
  const components = primeFactorize(scaled);
  return {
    baseValue: scaled,
    precisionFactor: base,
    components
  };
}

export function compareDepths(a: DepthDecomposition, b: DepthDecomposition): number {
  const sumA = a.components.reduce((acc, x) => acc + Math.log(x), 0);
  const sumB = b.components.reduce((acc, x) => acc + Math.log(x), 0);
  return sumA - sumB;
}

export type DepthLevel = 'shallow' | 'deep' | 'emergent';

export function classifyDepth(depth: DepthDecomposition): DepthLevel {
  const ln = depth.components.reduce((acc, val) => acc + Math.log(val), 0);
  if (ln > 19) return 'emergent';
  if (ln > 13) return 'deep';
  return 'shallow';
}

export function symbolizeComponents(components: number[]): string {
  const symbolMap: Record<number, string> = {
    2: '⚡',
    3: '🔥',
    5: '🌱',
    7: '🌊',
    11: '🌕',
    13: '🌀',
    17: '🌈'
  };
  return components.map(c => symbolMap[c] || `(${c})`).join(' · ');
}

export function depthToFrequencies(components: number[], baseHz: number = 440): number[] {
  return components.map(factor => baseHz * Math.pow(2, Math.log2(factor)));
}

export function depthToSigillinHint(depth: DepthDecomposition): string {
  const sum = depth.components.reduce((a, b) => a + Math.log(b), 0).toFixed(2);
  return `Tiefe lnSum ≈ ${sum}, Komponenten: ${symbolizeComponents(depth.components)}`;
}
