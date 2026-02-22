import { registerRoot } from 'remotion';

try {
    // Dynamic require to catch any import errors that would silently
    // prevent registerRoot from being called (causing delayRender timeout)
    const { RemotionRoot } = require('./Root');
    registerRoot(RemotionRoot);
} catch (error) {
    console.error('[ZODIAC] FATAL: Root component failed to load:', error);
    // Register a minimal fallback so Remotion doesn't hang for 3 minutes
    registerRoot(() => null);
}
