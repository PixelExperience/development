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
import { TraceType } from "common/trace/trace_type";
import {Parser} from "./parser";
import {ParserAccessibility} from "./parser_accessibility";
import {ParserInputMethodClients} from "./parser_input_method_clients";
import {ParserInputMethodManagerService} from "./parser_input_method_manager_service";
import {ParserInputMethodService} from "./parser_input_method_service";
import {ParserProtoLog} from "./parser_protolog";
import {ParserScreenRecording} from "./parser_screen_recording";
import {ParserScreenRecordingLegacy} from "./parser_screen_recording_legacy";
import {ParserSurfaceFlinger} from "./parser_surface_flinger";
import {ParserTransactions} from "./parser_transactions";
import {ParserWindowManager} from "./parser_window_manager";
import {ParserWindowManagerDump} from "./parser_window_manager_dump";

class ParserFactory {
  static readonly PARSERS = [
    ParserAccessibility,
    ParserInputMethodClients,
    ParserInputMethodManagerService,
    ParserInputMethodService,
    ParserProtoLog,
    ParserScreenRecording,
    ParserScreenRecordingLegacy,
    ParserSurfaceFlinger,
    ParserTransactions,
    ParserWindowManager,
    ParserWindowManagerDump,
  ];

  async createParsers(traces: File[]): Promise<[Parser[], ParserError[]]> {
    const parsers: Parser[] = [];
    const errors: ParserError[] = [];
    const completedParserTypes: any[] = [];

    for (const [index, trace] of traces.entries()) {
      console.log(`Loading trace #${index}`);
      const numberOfDetectedParsers = parsers.length;
      let repeatType = false;
      for (const ParserType of ParserFactory.PARSERS) {
        try {
          const parser = new ParserType(trace);
          await parser.parse();
          if (completedParserTypes.includes(ParserType)) {
            console.log(`Already successfully loaded a trace with parser type ${ParserType.name}`);
            repeatType = true;
            errors.push(new ParserError(trace, ParserErrorType.ALREADY_LOADED).setTraceType(parser.getTraceType()));
            break;
          } else {
            parsers.push(parser);
            completedParserTypes.push(ParserType);
            console.log(`Successfully loaded trace with parser type ${ParserType.name}`);
            break;
          }
        }
        catch(error) {
          console.log(`Failed to load trace with parser type ${ParserType.name}`);
        }
      }
      if (numberOfDetectedParsers === parsers.length && !repeatType) {
        errors.push(new ParserError(trace, ParserErrorType.UNSUPPORTED_FORMAT));
      }
    }

    return [parsers, errors];
  }
}

export enum ParserErrorType {
  ALREADY_LOADED,
  UNSUPPORTED_FORMAT
}

export class ParserError {
  public trace: File;
  public type: ParserErrorType;
  public traceType?: TraceType;
  constructor(trace: File, type: ParserErrorType) {
    this.trace = trace;
    this.type = type;
  }
  public setTraceType(traceType: TraceType) {
    this.traceType = traceType;
    return this;
  }
}

export {ParserFactory};