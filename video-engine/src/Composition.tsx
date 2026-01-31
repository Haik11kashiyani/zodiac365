import React from 'react';
import { AbsoluteFill, Audio, Img, Video, useVideoConfig, useCurrentFrame, interpolate, spring, Sequence } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';

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
    const { fps, durationInFrames } = useVideoConfig();

    return (
        <AbsoluteFill style={{ backgroundColor: 'black' }}>
            {/* BACKGROUND LAYER WITH TRANSITIONS */}
            <AbsoluteFill style={{ overflow: 'hidden' }}>
                 {/* Background clips with transition */}
                 {images && images.length > 0 && (
                    <TransitionSeries>
                        {images.map((imgSrc, index) => (
                            <TransitionSeries.Sequence key={index} durationInFrames={Math.floor(durationInFrames / images.length)}>
                                <BackgroundClip src={imgSrc} index={index} total={images.length} />
                            </TransitionSeries.Sequence>
                        ))}
                    </TransitionSeries>
                 )}
                 
                {/* Dark Overlay */}
                <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.4)' }} />
            </AbsoluteFill>

            {/* TEXT LAYER */}
            <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
                 <CaptionsLayer captions={captions} />
            </AbsoluteFill>
            
            {/* PROGRESS BAR */}
            <AbsoluteFill style={{ justifyContent: 'flex-end' }}>
                <div style={{
                    width: '100%',
                    height: '15px',
                    backgroundColor: 'rgba(255,255,255,0.2)'
                }}>
                    <div style={{
                        width: `${(frame / (30 * 60)) * 100}%`, // Assuming 60s max. Better: frame/durationInFrames
                        height: '100%',
                        backgroundColor: '#FFD700', // Gold
                        boxShadow: '0 0 10px #FFD700'
                    }} />
                </div>
            </AbsoluteFill>

            {/* AUDIO */}
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            {audioSrc && <Audio src={audioSrc} placeholder={null} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} />}
        </AbsoluteFill>
    );
};

const BackgroundClip: React.FC<{src: string, index: number, total: number}> = ({ src, index, total }) => {
    const frame = useCurrentFrame();
    
    // Smooth Scale Ken Burns
    const scale = interpolate(frame, [0, 150], [1.0, 1.15], { extrapolateRight: 'clamp' });
    
    // Fallback logic
    const finalSrc = src || "https://images.pexels.com/photos/1762851/pexels-photo-1762851.jpeg";
    const isVideo = finalSrc.endsWith('.mp4');
    
    const style = {
        width: '100%',
        height: '100%',
        objectFit: 'cover' as const,
        transform: `scale(${scale})`
    };

    if (isVideo) {
        return <Video src={finalSrc} style={style} muted loop />;
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return <Img src={finalSrc} style={style} placeholder={undefined} onResize={undefined} onResizeCapture={undefined} onPointerEnterCapture={undefined} onPointerLeaveCapture={undefined} />;
}

const CaptionsLayer: React.FC<{captions: Caption[]}> = ({ captions }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();
    const currentTime = frame / fps;

    const activeCaption = captions.find(c => currentTime >= c.start && currentTime <= c.end);

    if (!activeCaption) return null;
    
    // Calculate local frame for the caption to animate entry
    const captionStartFrame = activeCaption.start * fps;
    const timeInCaption = frame - captionStartFrame;
    
    // Pop-in spring
    const pop = spring({
        frame: timeInCaption,
        fps,
        config: { damping: 12, stiffness: 200 }
    });
    
    // Simple rotation wiggle
    const wiggle = Math.sin(timeInCaption * 0.1) * 2; 

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
            WebkitTextStroke: '3px black',
            transform: `scale(${pop}) rotate(${wiggle}deg)`
        }}>
            {activeCaption.text}
        </div>
    );
};
