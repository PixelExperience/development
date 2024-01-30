/*
 * Copyright (C) 2023 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {ArrayUtils} from 'common/array_utils';
import {FrameMap} from './frame_map';
import {
  AbsoluteEntryIndex,
  AbsoluteFrameIndex,
  EntriesRange,
  FramesRange,
  RelativeEntryIndex,
} from './index_types';
import {Parser} from './parser';
import {Timestamp, TimestampType} from './timestamp';
import {TraceType} from './trace_type';

export {
  AbsoluteEntryIndex,
  AbsoluteFrameIndex,
  EntriesRange,
  FramesRange,
  RelativeEntryIndex,
} from './index_types';

export class TraceEntry<T> {
  constructor(
    private readonly fullTrace: Trace<T>,
    private readonly parser: Parser<T>,
    private readonly index: AbsoluteEntryIndex,
    private readonly timestamp: Timestamp,
    private readonly framesRange: FramesRange | undefined
  ) {}

  getFullTrace(): Trace<T> {
    return this.fullTrace;
  }

  getIndex(): AbsoluteEntryIndex {
    return this.index;
  }

  getTimestamp(): Timestamp {
    return this.timestamp;
  }

  getFramesRange(): FramesRange | undefined {
    if (!this.fullTrace.hasFrameInfo()) {
      throw new Error(
        `Trace ${this.fullTrace.type} can't be accessed in frame domain (no frame info available)`
      );
    }
    return this.framesRange;
  }

  async getValue(): Promise<T> {
    return await this.parser.getEntry(this.index, this.timestamp.getType());
  }
}

export class Trace<T> {
  readonly type: TraceType;
  readonly lengthEntries: number;

  private readonly parser: Parser<T>;
  private readonly descriptors: string[];
  private readonly fullTrace: Trace<T>;
  private timestampType: TimestampType | undefined;
  private readonly entriesRange: EntriesRange;
  private frameMap?: FrameMap;
  private framesRange?: FramesRange;

  static newUninitializedTrace<T>(parser: Parser<T>): Trace<T> {
    return new Trace(
      parser.getTraceType(),
      parser,
      parser.getDescriptors(),
      undefined,
      undefined,
      undefined
    );
  }

  static newInitializedTrace<T>(
    type: TraceType,
    entryProvider: Parser<T>,
    descriptors: string[],
    timestampType: TimestampType,
    entriesRange: EntriesRange
  ): Trace<T> {
    return new Trace(type, entryProvider, descriptors, undefined, timestampType, entriesRange);
  }

  init(timestampType: TimestampType) {
    this.timestampType = timestampType;
  }

  private constructor(
    type: TraceType,
    parser: Parser<T>,
    descriptors: string[],
    fullTrace: Trace<T> | undefined,
    timestampType: TimestampType | undefined,
    entriesRange: EntriesRange | undefined
  ) {
    this.type = type;
    this.parser = parser;
    this.descriptors = descriptors;
    this.fullTrace = fullTrace ?? this;
    this.entriesRange = entriesRange ?? {start: 0, end: parser.getLengthEntries()};
    this.lengthEntries = this.entriesRange.end - this.entriesRange.start;
    this.timestampType = timestampType;
  }

  getDescriptors(): string[] {
    return this.parser.getDescriptors();
  }

  getTimestampType(): TimestampType {
    if (this.timestampType === undefined) {
      throw new Error('Trace no fully initialized yet!');
    }
    return this.timestampType;
  }

  setFrameInfo(frameMap: FrameMap, framesRange: FramesRange | undefined) {
    if (frameMap.lengthEntries !== this.fullTrace.lengthEntries) {
      throw new Error('Attemped to set a frame map with incompatible number of entries');
    }
    this.frameMap = frameMap;
    this.framesRange = framesRange;
  }

  hasFrameInfo(): boolean {
    return this.frameMap !== undefined;
  }

  getEntry(index: RelativeEntryIndex): TraceEntry<T> {
    const entry = this.convertToAbsoluteEntryIndex(index) as AbsoluteEntryIndex;
    if (entry < this.entriesRange.start || entry >= this.entriesRange.end) {
      throw new Error(
        `Trace entry's index out of bounds. Input relative index: ${index}. Slice length: ${this.lengthEntries}.`
      );
    }
    const frames = this.clampFramesRangeToSliceBounds(
      this.frameMap?.getFramesRange({start: entry, end: entry + 1})
    );
    return new TraceEntry<T>(
      this.fullTrace,
      this.parser,
      entry,
      this.getFullTraceTimestamps()[entry],
      frames
    );
  }

  getFrame(frame: AbsoluteFrameIndex): Trace<T> {
    this.checkTraceCanBeAccessedInFrameDomain();
    const entries = this.frameMap!.getEntriesRange({start: frame, end: frame + 1});
    return this.createSlice(entries, {start: frame, end: frame + 1});
  }

  findClosestEntry(time: Timestamp): TraceEntry<T> | undefined {
    this.checkTimestampIsCompatible(time);
    if (this.lengthEntries === 0) {
      return undefined;
    }

    const entry = this.clampEntryToSliceBounds(
      ArrayUtils.binarySearchFirstGreaterOrEqual(this.getFullTraceTimestamps(), time)
    );
    if (entry === undefined || entry === this.entriesRange.end) {
      return this.getEntry(this.lengthEntries - 1);
    }

    if (entry === this.entriesRange.start) {
      return this.getEntry(0);
    }

    const abs = (time: bigint) => (time < 0 ? -time : time);
    const timeDiff = abs(this.getFullTraceTimestamps()[entry].getValueNs() - time.getValueNs());
    const prevEntry = entry - 1;
    const prevTimeDiff = abs(
      this.getFullTraceTimestamps()[prevEntry].getValueNs() - time.getValueNs()
    );
    if (prevTimeDiff < timeDiff) {
      return this.getEntry(prevEntry - this.entriesRange.start);
    }
    return this.getEntry(entry - this.entriesRange.start);
  }

  findFirstGreaterOrEqualEntry(time: Timestamp): TraceEntry<T> | undefined {
    this.checkTimestampIsCompatible(time);
    if (this.lengthEntries === 0) {
      return undefined;
    }

    const pos = this.clampEntryToSliceBounds(
      ArrayUtils.binarySearchFirstGreaterOrEqual(this.getFullTraceTimestamps(), time)
    );
    if (pos === undefined || pos === this.entriesRange.end) {
      return undefined;
    }

    const entry = this.getEntry(pos - this.entriesRange.start);
    if (entry.getTimestamp() < time) {
      return undefined;
    }

    return entry;
  }

  findFirstGreaterEntry(time: Timestamp): TraceEntry<T> | undefined {
    this.checkTimestampIsCompatible(time);
    if (this.lengthEntries === 0) {
      return undefined;
    }

    const pos = this.clampEntryToSliceBounds(
      ArrayUtils.binarySearchFirstGreater(this.getFullTraceTimestamps(), time)
    );
    if (pos === undefined || pos === this.entriesRange.end) {
      return undefined;
    }

    const entry = this.getEntry(pos - this.entriesRange.start);
    if (entry.getTimestamp() <= time) {
      return undefined;
    }

    return entry;
  }

  findLastLowerOrEqualEntry(timestamp: Timestamp): TraceEntry<T> | undefined {
    if (this.lengthEntries === 0) {
      return undefined;
    }
    const firstGreater = this.findFirstGreaterEntry(timestamp);
    if (!firstGreater) {
      return this.getEntry(this.lengthEntries - 1);
    }
    if (firstGreater.getIndex() === this.entriesRange.start) {
      return undefined;
    }
    return this.getEntry(firstGreater.getIndex() - this.entriesRange.start - 1);
  }

  findLastLowerEntry(timestamp: Timestamp): TraceEntry<T> | undefined {
    if (this.lengthEntries === 0) {
      return undefined;
    }
    const firstGreaterOrEqual = this.findFirstGreaterOrEqualEntry(timestamp);
    if (!firstGreaterOrEqual) {
      return this.getEntry(this.lengthEntries - 1);
    }
    if (firstGreaterOrEqual.getIndex() === this.entriesRange.start) {
      return undefined;
    }
    return this.getEntry(firstGreaterOrEqual.getIndex() - this.entriesRange.start - 1);
  }

  sliceEntries(start?: RelativeEntryIndex, end?: RelativeEntryIndex): Trace<T> {
    const startEntry =
      this.clampEntryToSliceBounds(this.convertToAbsoluteEntryIndex(start)) ??
      this.entriesRange.start;
    const endEntry =
      this.clampEntryToSliceBounds(this.convertToAbsoluteEntryIndex(end)) ?? this.entriesRange.end;
    const entries: EntriesRange = {
      start: startEntry,
      end: endEntry,
    };
    const frames = this.frameMap?.getFramesRange(entries);
    return this.createSlice(entries, frames);
  }

  sliceTime(start?: Timestamp, end?: Timestamp): Trace<T> {
    this.checkTimestampIsCompatible(start);
    this.checkTimestampIsCompatible(end);
    const startEntry =
      start === undefined
        ? this.entriesRange.start
        : this.clampEntryToSliceBounds(
            ArrayUtils.binarySearchFirstGreaterOrEqual(this.getFullTraceTimestamps(), start)
          ) ?? this.entriesRange.end;
    const endEntry =
      end === undefined
        ? this.entriesRange.end
        : this.clampEntryToSliceBounds(
            ArrayUtils.binarySearchFirstGreaterOrEqual(this.getFullTraceTimestamps(), end)
          ) ?? this.entriesRange.end;
    const entries: EntriesRange = {
      start: startEntry,
      end: endEntry,
    };
    const frames = this.frameMap?.getFramesRange(entries);
    return this.createSlice(entries, frames);
  }

  sliceFrames(start?: AbsoluteFrameIndex, end?: AbsoluteFrameIndex): Trace<T> {
    this.checkTraceCanBeAccessedInFrameDomain();
    if (!this.framesRange) {
      return this.createSlice(undefined, undefined);
    }
    const frames: FramesRange = {
      start: this.clampFrameToSliceBounds(start) ?? this.framesRange.start,
      end: this.clampFrameToSliceBounds(end) ?? this.framesRange.end,
    };
    const entries = this.frameMap!.getEntriesRange(frames);
    return this.createSlice(entries, frames);
  }

  forEachEntry(callback: (pos: TraceEntry<T>, index: RelativeEntryIndex) => void) {
    for (let index = 0; index < this.lengthEntries; ++index) {
      callback(this.getEntry(index), index);
    }
  }

  mapEntry<U>(callback: (entry: TraceEntry<T>, index: RelativeEntryIndex) => U): U[] {
    const result: U[] = [];
    this.forEachEntry((entry, index) => {
      result.push(callback(entry, index));
    });
    return result;
  }

  forEachTimestamp(callback: (timestamp: Timestamp, index: RelativeEntryIndex) => void) {
    const timestamps = this.getFullTraceTimestamps();
    for (let index = 0; index < this.lengthEntries; ++index) {
      callback(timestamps[this.entriesRange.start + index], index);
    }
  }

  forEachFrame(callback: (frame: Trace<T>, index: AbsoluteFrameIndex) => void) {
    this.checkTraceCanBeAccessedInFrameDomain();
    if (!this.framesRange) {
      return;
    }
    for (let frame = this.framesRange.start; frame < this.framesRange.end; ++frame) {
      callback(this.getFrame(frame), frame);
    }
  }

  mapFrame<U>(callback: (frame: Trace<T>, index: AbsoluteFrameIndex) => U): U[] {
    const result: U[] = [];
    this.forEachFrame((traces, index) => {
      result.push(callback(traces, index));
    });
    return result;
  }

  getFramesRange(): FramesRange | undefined {
    this.checkTraceCanBeAccessedInFrameDomain();
    return this.framesRange;
  }

  private getFullTraceTimestamps(): Timestamp[] {
    if (this.timestampType === undefined) {
      throw new Error('Forgot to initialize trace?');
    }

    const timestamps = this.parser.getTimestamps(this.timestampType);
    if (!timestamps) {
      throw new Error(`Timestamp type ${this.timestampType} is expected to be available`);
    }
    return timestamps;
  }

  private convertToAbsoluteEntryIndex(
    index: RelativeEntryIndex | undefined
  ): AbsoluteEntryIndex | undefined {
    if (index === undefined) {
      return undefined;
    }
    if (index < 0) {
      return this.entriesRange.end + index;
    }
    return this.entriesRange.start + index;
  }

  private createSlice(
    entries: EntriesRange | undefined,
    frames: FramesRange | undefined
  ): Trace<T> {
    entries = this.clampEntriesRangeToSliceBounds(entries);
    frames = this.clampFramesRangeToSliceBounds(frames);

    if (entries === undefined || entries.start >= entries.end) {
      entries = {
        start: this.entriesRange.end,
        end: this.entriesRange.end,
      };
    }

    const slice = new Trace<T>(
      this.type,
      this.parser,
      this.descriptors,
      this.fullTrace,
      this.timestampType,
      entries
    );

    if (this.frameMap) {
      slice.setFrameInfo(this.frameMap, frames);
    }

    return slice;
  }

  private clampEntriesRangeToSliceBounds(
    entries: EntriesRange | undefined
  ): EntriesRange | undefined {
    if (entries === undefined) {
      return undefined;
    }
    return {
      start: this.clampEntryToSliceBounds(entries.start) as AbsoluteEntryIndex,
      end: this.clampEntryToSliceBounds(entries.end) as AbsoluteEntryIndex,
    };
  }

  private clampFramesRangeToSliceBounds(frames: FramesRange | undefined): FramesRange | undefined {
    if (frames === undefined) {
      return undefined;
    }
    return {
      start: this.clampFrameToSliceBounds(frames.start) as AbsoluteFrameIndex,
      end: this.clampFrameToSliceBounds(frames.end) as AbsoluteFrameIndex,
    };
  }

  private clampEntryToSliceBounds(
    entry: AbsoluteEntryIndex | undefined
  ): AbsoluteEntryIndex | undefined {
    if (entry === undefined) {
      return undefined;
    }
    return Math.min(Math.max(entry, this.entriesRange.start), this.entriesRange.end);
  }

  private clampFrameToSliceBounds(
    frame: AbsoluteFrameIndex | undefined
  ): AbsoluteFrameIndex | undefined {
    if (!this.framesRange || frame === undefined) {
      return undefined;
    }

    if (frame < 0) {
      throw new Error(`Absolute frame index cannot be negative. Found '${frame}'`);
    }

    return Math.min(Math.max(frame, this.framesRange.start), this.framesRange.end);
  }

  private checkTraceCanBeAccessedInFrameDomain() {
    if (!this.frameMap) {
      throw new Error(
        `Trace ${this.type} can't be accessed in frame domain (no frame mapping available)`
      );
    }
  }

  private checkTimestampIsCompatible(timestamp?: Timestamp) {
    if (!timestamp) {
      return;
    }
    const timestamps = this.parser.getTimestamps(timestamp.getType());
    if (timestamps === undefined) {
      throw new Error(
        `Trace ${this.type} can't be accessed using timestamp of type ${timestamp.getType()}`
      );
    }
  }
}
