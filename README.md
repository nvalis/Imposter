# Imposter
Some code for the reddit r/imposter game.

## API

### /room (GET)

Contains 5 notes to choose from with `text` and `note-id`:
```html
<gremlin-note id="$(note-id)">$(text)</gremlin-note>
```

A `CSRF-token` is given:
```html
<gremlin-app csrf="$(CSRF-token)">
```

### /submit_guess (POST)

Expects `note-id` and `CSRF-token`:
```json
{"undefined": "undefined", "note_id": $(note-id), "csrf_token": $(CSRF-token)}
```

### /create_note (GET/POST)

Use GET request to receive the `CSRF-token` and then submit your `note` with POST:
```json
{"note": $(note), "csrf_token": $(CSRF-token)}
```

There seems to be a time limit for this endpoint of 3 minutes.
