/*
 * Copyright (C) 2022 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANYf KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {assertDefined} from 'common/assert_utils';
import {TracesBuilder} from 'test/unit/traces_builder';
import {TraceBuilder} from 'test/unit/trace_builder';
import {LogMessage} from 'trace/protolog';
import {RealTimestamp} from 'trace/timestamp';
import {Trace} from 'trace/trace';
import {Traces} from 'trace/traces';
import {TracePosition} from 'trace/trace_position';
import {TraceType} from 'trace/trace_type';
import {Presenter} from './presenter';
import {UiData, UiDataMessage} from './ui_data';

describe('ViewerProtoLogPresenter', () => {
  let presenter: Presenter;
  let inputMessages: UiDataMessage[];
  let trace: Trace<LogMessage>;
  let position10: TracePosition;
  let position11: TracePosition;
  let position12: TracePosition;
  let outputUiData: undefined | UiData;

  beforeEach(async () => {
    const time10 = new RealTimestamp(10n);
    const time11 = new RealTimestamp(11n);
    const time12 = new RealTimestamp(12n);

    inputMessages = [
      new LogMessage('text0', 'time', 'tag0', 'level0', 'sourcefile0', 10n),
      new LogMessage('text1', 'time', 'tag1', 'level1', 'sourcefile1', 11n),
      new LogMessage('text2', 'time', 'tag2', 'level2', 'sourcefile2', 12n),
    ].map((message, index) => {
      (message as UiDataMessage).originalIndex = index;
      return message as UiDataMessage;
    });

    trace = new TraceBuilder<LogMessage>()
      .setEntries(inputMessages)
      .setTimestamps([time10, time11, time12])
      .build();

    position10 = TracePosition.fromTimestamp(time10);
    position11 = TracePosition.fromTimestamp(time11);
    position12 = TracePosition.fromTimestamp(time12);

    outputUiData = undefined;

    const traces = new Traces();
    traces.setTrace(TraceType.PROTO_LOG, trace);
    presenter = new Presenter(traces, (data: UiData) => {
      outputUiData = data;
    });
    await presenter.onTracePositionUpdate(position10); // trigger initialization
  });

  it('is robust to empty trace', async () => {
    const traces = new TracesBuilder().setEntries(TraceType.PROTO_LOG, []).build();
    presenter = new Presenter(traces, (data: UiData) => {
      outputUiData = data;
    });

    expect(assertDefined(outputUiData).messages).toEqual([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toBeUndefined();

    await presenter.onTracePositionUpdate(position10);
    expect(assertDefined(outputUiData).messages).toEqual([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toBeUndefined();
  });

  it('processes trace position updates', async () => {
    await presenter.onTracePositionUpdate(position10);

    expect(assertDefined(outputUiData).allLogLevels).toEqual(['level0', 'level1', 'level2']);
    expect(assertDefined(outputUiData).allTags).toEqual(['tag0', 'tag1', 'tag2']);
    expect(assertDefined(outputUiData).allSourceFiles).toEqual([
      'sourcefile0',
      'sourcefile1',
      'sourcefile2',
    ]);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);
  });

  it('updates displayed messages according to log levels filter', () => {
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onLogLevelsFilterChanged([]);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onLogLevelsFilterChanged(['level1']);
    expect(assertDefined(outputUiData).messages).toEqual([inputMessages[1]]);

    presenter.onLogLevelsFilterChanged(['level0', 'level1', 'level2']);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);
  });

  it('updates displayed messages according to tags filter', () => {
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onTagsFilterChanged([]);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onTagsFilterChanged(['tag1']);
    expect(assertDefined(outputUiData).messages).toEqual([inputMessages[1]]);

    presenter.onTagsFilterChanged(['tag0', 'tag1', 'tag2']);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);
  });

  it('updates displayed messages according to source files filter', () => {
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onSourceFilesFilterChanged([]);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onSourceFilesFilterChanged(['sourcefile1']);
    expect(assertDefined(outputUiData).messages).toEqual([inputMessages[1]]);

    presenter.onSourceFilesFilterChanged(['sourcefile0', 'sourcefile1', 'sourcefile2']);
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);
  });

  it('updates displayed messages according to search string filter', () => {
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onSearchStringFilterChanged('');
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onSearchStringFilterChanged('text');
    expect(assertDefined(outputUiData).messages).toEqual(inputMessages);

    presenter.onSearchStringFilterChanged('text0');
    expect(assertDefined(outputUiData).messages).toEqual([inputMessages[0]]);

    presenter.onSearchStringFilterChanged('text1');
    expect(assertDefined(outputUiData).messages).toEqual([inputMessages[1]]);
  });

  it('computes current message index', async () => {
    // Position -> entry #0
    await presenter.onTracePositionUpdate(position10);
    presenter.onLogLevelsFilterChanged([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);

    presenter.onLogLevelsFilterChanged(['level0']);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);

    presenter.onLogLevelsFilterChanged([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);

    // Position -> entry #1
    await presenter.onTracePositionUpdate(position11);
    presenter.onLogLevelsFilterChanged([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(1);

    presenter.onLogLevelsFilterChanged(['level0']);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);

    presenter.onLogLevelsFilterChanged(['level1']);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(0);

    presenter.onLogLevelsFilterChanged(['level0', 'level1']);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(1);

    // Position -> entry #2
    await presenter.onTracePositionUpdate(position12);
    presenter.onLogLevelsFilterChanged([]);
    expect(assertDefined(outputUiData).currentMessageIndex).toEqual(2);
  });
});
