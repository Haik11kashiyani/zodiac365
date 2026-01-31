import React from 'react';
import { AbsoluteFill, Audio, Img, Video, useVideoConfig, useCurrentFrame, interpolate } from 'remotion';

interface Caption {
    start: number;
    end: number;
    text: string;
}

interface ZodiacCompositionProps {
    scriptText: string;
    audioSrc: string;
    captions: Caption[];
    images: string[];
}

export const ZodiacComposition: React.FC<ZodiacCompositionProps> = ({ scriptText, audioSrc, captions, images }) => {
    const frame = useCurrentFrame(); 
    
    // Background Media (Video or Image)
    const mediaDuration = 150; // Switch every 5s
    const currentMediaIndex = Math.floor(frame / mediaDuration) % Math.max(images.length, 1);
    const currentMedia = images[currentMediaIndex] || "https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg";
    
    const isVideo = currentMedia.endsWith('.mp4');

    const scale = interpolate(
        frame % mediaDuration,
        [0, mediaDuration],
        [1.1, 1.2] 
    );

    return (
        <AbsoluteFill style={{ backgroundColor: 'black' }}>
            {/* BACKGROUND LAYER */}
            <AbsoluteFill style={{ overflow: 'hidden' }}>
                 {isVideo ? (
                    <Video
                        src={currentMedia}
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            transform: `scale(${scale})`
                        }}
                        muted // Background video should be muted
                        loop
                    />
                 ) : (
                    <Img 
                        src={currentMedia} 
                        style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover',
                            transform: `scale(${scale})`
                        }}
                    />
                 )}
                <div style={{
                    position: 'absolute',
                    top: 0, 
                    left: 0,
                    width: '100%', 
                    height: '100%',
                    backgroundColor: 'rgba(0,0,0,0.4)' 
                }} />
            </AbsoluteFill>

            {/* TEXT LAYER */}
            <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
                 <CaptionsLayer captions={captions} />
            </AbsoluteFill>

            {/* AUDIO */}
            {audioSrc && <Audio src={audioSrc} />}
        </AbsoluteFill>
    );
};

const CaptionsLayer: React.FC<{captions: Caption[]}> = ({ captions }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const currentTime = frame / fps;

    const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);

    if (!activeCaption) return null;

    return (
        <div style={{
            fontFamily: 'Montserrat, sans-serif',
            fontWeight: 900,
            fontSize: '85px',
            textAlign: 'center',
            color: 'white',
            textTransform: 'uppercase',
            maxWidth: '90%',
            lineHeight: '1.0',
            textShadow: '5px 5px 0px #000000',
            WebkitTextStroke: '3px black' // Hormozi Stroke
        }}>
            {activeCaption.text}
        </div>
    );
};
