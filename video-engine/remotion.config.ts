import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 300 seconds to handle large public dirs with image sequences
Config.setDelayRenderTimeoutInMilliseconds(300000);

// Use 1 concurrent thread on CI to prevent RAM exhaustion and deadlocks
Config.setConcurrency(1);
