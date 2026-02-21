import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 90 seconds - kills stuck asset loads fast instead of hanging for 10 min
Config.setDelayRenderTimeoutInMilliseconds(90000);
