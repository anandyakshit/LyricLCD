import asyncio
import re
import time
import requests
import serial
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

#Variables
Lyric_OffSet= 1.25
srl=serial.Serial("COM3", 9600)
time.sleep(2) #relaxation time for arduino to accept serial data

# LRCLIB

def fetch_lyrics(title, artist):
    url = "https://lrclib.net/api/search"

    params = {
        "track_name": title,
        "artist_name": artist
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    results = response.json()

    if not results:
        return None

    for item in results:
        if item.get("syncedLyrics"):
            return item["syncedLyrics"]

    return None


# LRC Parsing

def parse_lrc(lrc_text):
    lyrics = []
    pattern = r"\[(\d+):(\d+\.\d+)\](.*)"

    for line in lrc_text.splitlines():
        match = re.match(pattern, line)

        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            text = match.group(3).strip()
            timestamp = minutes * 60 + seconds
            lyrics.append((timestamp, text))

    return lyrics

def get_current_lyric_info(lyrics, elapsed_seconds):
    current_text = ""
    current_time = 0
    next_time = None

    for i in range(len(lyrics)):
        timestamp, text = lyrics[i]

        if elapsed_seconds >= timestamp:
            current_time = timestamp
            current_text = text

            if i + 1 < len(lyrics):
                next_time = lyrics[i + 1][0]
            else:
                next_time = timestamp + 3
        else:
            break

    return current_text, current_time, next_time


#Media Session Detection (Update it later Dumbass)

async def get_current_session():
    
    sessions = await MediaManager.request_async()
    current = sessions.get_current_session()
    return current

#word wrapping so the display doesnt overflow
def wrap_text(text, width=16):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if current_line == "":
            current_line = word
        elif len(current_line) + 1 + len(word) <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

#lcd page forming code

def make_lcd_pages(text, width=16):
    wrapped = wrap_text(text, width)

    pages = []

    for i in range(0, len(wrapped), 2):
        line1 = wrapped[i]
        line2 = wrapped[i + 1] if i + 1 < len(wrapped) else ""

        pages.append((line1, line2))

    return pages

#main

async def main():

    print("Waiting for Media Session...")
    current = await get_current_session()

    if not current:
        print("No active media session found.")
        return

    info = await current.try_get_media_properties_async()
    title = info.title
    artist = info.artist
    print(f"\nSong  : {title}")
    print(f"Artist: {artist}")
    print("\nFetching lyrics...")
    lrc = fetch_lyrics(title, artist)

    if not lrc:
        print("No synced lyrics found.")
        return
    
    lyrics = parse_lrc(lrc)
    print(f"Loaded {len(lyrics)} lyric lines.\n")
    last_packet = ""

    while True:

        try:

            timeline = current.get_timeline_properties()
            elapsed = timeline.position.total_seconds() + Lyric_OffSet
            line, current_time, next_time = get_current_lyric_info(lyrics, elapsed)

            mins = int(elapsed // 60)
            secs = int(elapsed % 60)

            if line:
                pages = make_lcd_pages(line)

                if pages:
                    duration = next_time - current_time
                    time_inside_line = elapsed - current_time

                    page_duration = duration / len(pages)

                    page_index = int(time_inside_line // page_duration)

                    if page_index >= len(pages):
                        page_index = len(pages) - 1

                    lcd_line1, lcd_line2 = pages[page_index]

                    packet = lcd_line1 + "|" + lcd_line2 + "\n"

                    if packet != last_packet:

                        srl.write(packet.encode("utf-8"))

                        print(
                f"[{mins:02}:{secs:02}] "
                f"{lcd_line1} / {lcd_line2}"
            )

            last_packet = packet
            await asyncio.sleep(0.5)

        except KeyboardInterrupt:
            print("\nStopped.")
            break

        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
