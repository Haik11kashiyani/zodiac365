import { registerRoot } from 'remotion';
import { RemotionRoot } from './Root';

// Static import is required for Remotion's multi-page rendering (concurrency > 1).
// Using require() in a try-catch breaks webpack's module evaluation order,
// causing the second browser page to fail registerRoot detection.
registerRoot(RemotionRoot);
