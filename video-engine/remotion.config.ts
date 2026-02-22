import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 180 seconds to handle large public dirs with image sequences
Config.setDelayRenderTimeoutInMilliseconds(180000);
