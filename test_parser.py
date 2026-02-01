import re

def parse_vtt(vtt_file):
    captions = []
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})')
    for i, line in enumerate(lines):
        line = line.strip()
        match = time_pattern.match(line)
        if match:
            h, m, s, ms = map(int, match.groups()[0:4])
            start_sec = h*3600 + m*60 + s + ms/1000.0
            h, m, s, ms = map(int, match.groups()[4:8])
            end_sec = h*3600 + m*60 + s + ms/1000.0
            if i + 1 < len(lines):
                text = lines[i+1].strip()
                if text:
                    words = text.split()
                    chunk_size = 2
                    chunks = [' '.join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
                    duration = end_sec - start_sec
                    chunk_duration = duration / len(chunks)
                    for k, chunk in enumerate(chunks):
                        c_start = start_sec + (k * chunk_duration)
                        c_end = c_start + chunk_duration
                        captions.append({'start': c_start, 'end': c_end, 'text': chunk.upper()})
    return captions

if __name__ == "__main__":
    result = parse_vtt('test.vtt')
    print(f"Found {len(result)} captions:")
    for c in result:
        print(c)
