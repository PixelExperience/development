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
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import {Timestamp, TimestampType} from "common/trace/timestamp";
import {TraceType} from "common/trace/trace_type";
import {Parser} from "./parser";
import {InputMethodClientsTraceFileProto} from "./proto_types";

class ParserInputMethodClients extends Parser {
  constructor(trace: Blob) {
    super(trace);
  }

  getTraceType(): TraceType {
    return TraceType.INPUT_METHOD_CLIENTS;
  }

  override getMagicNumber(): number[] {
    return ParserInputMethodClients.MAGIC_NUMBER;
  }

  override decodeTrace(buffer: Uint8Array): any[] {
    return (<any>InputMethodClientsTraceFileProto.decode(buffer)).entry;
  }

  override getTimestamp(entryProto: any, type: TimestampType): undefined|Timestamp {
    if (type !== TimestampType.ELAPSED) {
      return undefined;
    }
    return new Timestamp(type, BigInt(entryProto.elapsedRealtimeNanos));
  }

  override processDecodedEntry(entryProto: any): any {
    return entryProto;
  }

  private static readonly MAGIC_NUMBER = [0x09, 0x49, 0x4d, 0x43, 0x54, 0x52, 0x41, 0x43, 0x45]; // .IMCTRACE
}

export {ParserInputMethodClients};
