<!-- fonte: https://developer.apple.com/tutorials/data/documentation/appkit/nsglasseffectcontainerview.json -->

# NSGlassEffectContainerView

*Class* · macOS

A view that efficiently merges descendant glass effect views together when they are within a specified proximity to each other.

```swift
class NSGlassEffectContainerView
```

### Overview

> **Tip:** Using a glass effect container view can improve performance by reducing the number of passes required to render similar glass effect views.

## Instance Properties

- `contentView` — The view that contains descendant views to merge together when in proximity to each other.
- `spacing` — The proximity at which the glass effect container view begins merging eligible descendent glass effect views.
