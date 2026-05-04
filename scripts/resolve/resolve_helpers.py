#!/usr/bin/env python3
"""
Reusable DaVinci Resolve scripting helpers.

Usage:
    import sys
    sys.path.insert(0, '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules')
    from resolve_helpers import get_resolve, get_project, get_media_pool, get_timeline
    from resolve_helpers import import_media_to_bin, tag_clips_from_jsonl, add_timeline_markers

Requires DaVinci Resolve Studio running.

IMPORTANT — Resolve metadata gotchas:
  1. Use key-value SetMetadata(key, value), NOT dict form SetMetadata({dict}) — dict silently fails in Resolve 20.
  2. CSV separators must be comma-only: "a,b,c" NOT "a, b, c" — spaces create duplicate Smart Bins.
  3. Always normalize singular to plural (ants not ant) — see KEYWORD_NORMALIZE dict.
"""

import os, sys, json

sys.path.insert(0, '/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules')

def get_resolve():
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp('Resolve')
    if not resolve:
        raise ConnectionError("Cannot connect to Resolve. Is Resolve Studio running?")
    return resolve

def get_project(resolve=None):
    resolve = resolve or get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        raise RuntimeError("No project open")
    return proj

def get_media_pool(resolve=None):
    proj = get_project(resolve)
    return proj.GetMediaPool()

def get_timeline(resolve=None):
    proj = get_project(resolve)
    tl = proj.GetCurrentTimeline()
    if not tl:
        raise RuntimeError("No timeline active")
    return tl


def navigate_to_folder(mp, path):
    """Navigate to a media pool folder by path like 'Master/Round 3 - Simple'."""
    root = mp.GetRootFolder()
    mp.SetCurrentFolder(root)
    parts = path.replace("Master/", "").split("/")
    current = root
    for part in parts:
        if not part:
            continue
        found = False
        for sub in current.GetSubFolderList():
            if sub.GetName() == part:
                mp.SetCurrentFolder(sub)
                current = sub
                found = True
                break
        if not found:
            raise FileNotFoundError(f"Folder not found: {part} (in path {path})")
    return current


def import_media_to_bin(folder_path, file_paths, resolve=None):
    """Import media files into a specific media pool folder.
    
    Args:
        folder_path: e.g. "Master/Round 3 - Simple"
        file_paths: list of absolute file paths
    Returns:
        list of imported MediaPoolItem objects
    """
    mp = get_media_pool(resolve)
    navigate_to_folder(mp, folder_path)
    items = mp.ImportMedia(file_paths)
    if not items:
        return []
    return items


def get_clips_in_folder(folder_path, resolve=None):
    """Get all clips in a media pool folder.
    
    Returns:
        list of dicts with 'name', 'id', 'item' (the MediaPoolItem object)
    """
    mp = get_media_pool(resolve)
    folder = navigate_to_folder(mp, folder_path)
    clips = folder.GetClipList()
    result = []
    for clip in clips:
        result.append({
            "name": clip.GetName(),
            "id": clip.GetUniqueId(),
            "item": clip,
        })
    return result


KEYWORD_NORMALIZE = {
    "ant": "ants",
    "clock": "clocks",
    "figure": "figures",
    "lamp": "lamps",
    "leaf": "leaves",
    "star": "stars",
    "building": "buildings",
    "newspaper": "newspapers",
    "sheet": "sheets",
    "miniature": "miniatures",
}

def sanitize_tag(value):
    """Clean a metadata tag value.
    
    - Strip whitespace
    - Collapse double spaces
    - Remove empty CSV parts
    - Deduplicate tags
    - Normalize singular/plural (always use canonical plural form)
    """
    if not value:
        return ""
    value = value.strip()
    value = " ".join(value.split())
    parts = [p.strip() for p in value.split(",")]
    parts = [p for p in parts if p]
    parts = [KEYWORD_NORMALIZE.get(p, p) for p in parts]
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    return ",".join(seen)


def set_clip_metadata(item, metadata):
    """Set metadata on a clip using key-value calls (dict form is unreliable in Resolve 20).
    Values are sanitized automatically.
    
    Args:
        item: MediaPoolItem object
        metadata: dict of {field: value}, e.g. {"Comments": "s1", "Keywords": "myna, ants"}
    Returns:
        True if all fields set successfully
    """
    all_ok = True
    for key, value in metadata.items():
        clean = sanitize_tag(value)
        if not item.SetMetadata(key, clean):
            all_ok = False
    return all_ok


def tag_clips_from_jsonl(folder_path, jsonl_path, resolve=None):
    """Apply metadata tags to clips from a JSONL file.
    
    Each line in the JSONL: {"filename": "clip.mp4", "Comments": "s1", "Keywords": "myna, ants", "Description": "street"}
    Values are sanitized (trimmed, deduped, no empty parts).
    Uses key-value SetMetadata calls (dict form is unreliable in Resolve 20).
    
    Args:
        folder_path: media pool folder path
        jsonl_path: path to JSONL file with tags
    Returns:
        (success_count, fail_count)
    """
    clips = get_clips_in_folder(folder_path, resolve)
    clip_map = {c["name"]: c["item"] for c in clips}
    
    ok = fail = 0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            filename = data.pop("filename")
            if filename in clip_map:
                item = clip_map[filename]
                if set_clip_metadata(item, data):
                    ok += 1
                    print(f"  OK: {filename}")
                else:
                    fail += 1
                    print(f"  FAIL: {filename}")
            else:
                fail += 1
                print(f"  SKIP (not found in bin): {filename}")
    return ok, fail


def add_timeline_markers(markers, resolve=None):
    """Add markers to the current timeline.
    
    Args:
        markers: list of dicts with 'frame', 'color', 'name', 'note', 'duration' (optional, default 1)
    Returns:
        (success_count, fail_count)
    """
    tl = get_timeline(resolve)
    ok = fail = 0
    for m in markers:
        result = tl.AddMarker(
            m["frame"],
            m["color"],
            m["name"],
            m.get("note", ""),
            m.get("duration", 1),
            m.get("custom_data", "")
        )
        if result:
            ok += 1
            print(f"  OK: frame {m['frame']} — {m['name']}")
        else:
            fail += 1
            print(f"  FAIL: frame {m['frame']} — {m['name']}")
    return ok, fail


def create_timeline_with_audio(timeline_name, audio_clip_name, folder_path="Master/Audio", resolve=None):
    """Create a timeline and append an audio clip to it.
    
    Returns:
        the Timeline object
    """
    mp = get_media_pool(resolve)
    
    # Create empty timeline
    mp.SetCurrentFolder(mp.GetRootFolder())
    tl = mp.CreateEmptyTimeline(timeline_name)
    if not tl:
        raise RuntimeError(f"Failed to create timeline: {timeline_name}")
    
    # Find the audio clip
    audio_folder = navigate_to_folder(mp, folder_path)
    audio_clips = audio_folder.GetClipList()
    audio_item = None
    for clip in audio_clips:
        if clip.GetName() == audio_clip_name:
            audio_item = clip
            break
    
    if not audio_item:
        print(f"Warning: audio clip '{audio_clip_name}' not found in {folder_path}")
        return tl
    
    # Append audio to timeline
    result = mp.AppendToTimeline([audio_item])
    if result:
        print(f"  Audio '{audio_clip_name}' added to timeline '{timeline_name}'")
    else:
        print(f"  Warning: failed to append audio to timeline")
    
    return tl


if __name__ == "__main__":
    resolve = get_resolve()
    proj = get_project(resolve)
    print(f"Connected to: {resolve.GetProductName()} {resolve.GetVersionString()}")
    print(f"Project: {proj.GetName()}")
