---
title: "SoundMat (1) Idea"
docLang: en
translationKey: soundmat-1-idea
alternates:
  zh: /soundmat/soundmat-1-idea/
  en: /soundmat/en/soundmat-1-idea/
aliases:
  - /soundmat/en/soundmat-1-idea/
---

I set four criteria to decide what product I actually wanted to build:

1. Something I could realistically build
2. Something I found genuinely fun and interesting
3. Something usable—you could see it working
4. Something with real need or clear application potential

On the first point: because this was a course project with a small team, the device had to stay compact and low-cost.

On the second: the project had to be playful—something I could enjoy myself and that would make others’ eyes light up when I showed it.

On the third: the effect had to be visible and compelling. The design should not disappear behind code, jargon, or dry metrics. People should get it at a glance and think, *that’s really cool*.

On the fourth: I’ve done too many projects that were pure faux needs—built for the sake of building. Afterward, all you might have is a technical takeaway. I can’t stand that anymore. Real need or application potential changes everything: the project has room to grow, and the sense of meaning is completely different.


UW EE 546C asks us to design and build an interactive hardware product based on a tactile sensing system.

In that context, glove-style or pressure-tactile systems felt like the best fit—the instructor researches this area, the direction is clear, and complexity is manageable. So the broad direction became pressure-based touch sensing.

I also love music, so combining music with touch sensing became an important line of thought.

At first I considered glove-based virtual instruments—a classic HCI theme that seemed to satisfy all four criteria. But the learning curve felt high, and it didn’t feel very novel. Still, the key insight for me was ensemble play: many people wearing gloves and playing together.

While brainstorming, I read about Dynamicland, the HCI classic about interacting with objects in the environment—and wondered: *what if physical objects could play music?*

That became SoundMat: a circular mat where everyone places objects on top. Performance is loop-based; parameters come from object size, weight, and distance from the center. Musical layers can be notes, harmony, drums, rhythm.

Concretely: a virtual scan line runs from the center to the rim and rotates continuously. Whenever it hits an object, it triggers sound. Concentric rings map to different musical elements—different instruments, for example.

I had Claude write a one-minute demo in about a minute.

The design hinges on a few things:

First, interaction must stay simple. This is not a pro instrument—it’s for casual play. Even beginners should understand what they hear.

Second, the music should sound good no matter what—yet still change. Those two goals tension each other; different modes might resolve that later.

Third, feedback must be immediate, obvious, and high quality. That’s what separates boring from fun.

SoundMat met those three points well. Implementation is relatively straightforward, but it’s very fun, the effect lands, and the potential is real.

It also has a social dimension—naturally a device for multi-person improvised music.

Another strength: it fits public installation art—airports, galleries, shared spaces. Installations succeed through co-creation; this design supports that like a musical campfire: people gather, and music appears.

I asked Claude whether anything similar existed. Yes—Reactable (2005), Prix Ars Electronica gold: round table, objects on surface, multi-user collaboration, very close in form. But Reactable targets professional musicians; SoundMat is for zero-experience co-creation.

(Written April 9, 2026, early morning)

Next: [SoundMat (2) Product Design Philosophy](/soundmat/en/soundmat-2-philosophy/)
