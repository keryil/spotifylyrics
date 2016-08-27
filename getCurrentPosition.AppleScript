set currentlyPlayingTrack to getCurrentlyPlayingTrack()

-- Method to get the current position of the playing track
on getCurrentlyPlayingTrack()
  tell application "Spotify"
    set pos to player position
    return pos
  end tell
end getCurrentlyPlayingTrack