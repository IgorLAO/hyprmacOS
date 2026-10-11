<!-- fonte: https://developer.apple.com/tutorials/data/documentation/swiftui/view/glasseffectid(_:in:).json -->

# glassEffectID(_:in:)

*Instance Method* · iOS, iPadOS, Mac Catalyst, macOS, tvOS, watchOS

Associates an identity value to Liquid Glass effects defined within this view.

```swift
nonisolated func glassEffectID(_ id: (some Hashable & Sendable)?, in namespace: Namespace.ID) -> some View

```

### Discussion

You use this modifier with the `glassEffect(_:in:)` view modifier and a `GlassEffectContainer` view. When used together, SwiftUI uses the identifier to animate shapes to and from each other during transitions.
