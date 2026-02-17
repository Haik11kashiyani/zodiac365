import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 2 minutes per frame is generous but catches truly stuck renders
Config.setDelayRenderTimeoutInMilliseconds(120000);
