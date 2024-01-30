/*
 * Copyright 2020, The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {shortenName} from '../mixin';

import {
  Configuration,
  ConfigurationContainer,
  toRect,
  WindowConfiguration,
  WindowContainer,
} from '../common';

import {Activity} from './Activity';
import {DisplayArea} from './DisplayArea';
import {DisplayContent} from './DisplayContent';
import {Task} from './Task';
import {TaskFragment} from './TaskFragment';
import {WindowState} from './WindowState';
import {WindowToken} from './WindowToken';

WindowContainer.fromProto = (
  proto: any,
  protoChildren: any[],
  isActivityInTree: boolean,
  nextSeq: () => number,
  nameOverride: string | null = null,
  identifierOverride: string | null = null,
  tokenOverride: any = null,
  visibleOverride: boolean | null = null
): WindowContainer => {
  if (proto == null) {
    return null;
  }

  const containerOrder = nextSeq();
  const children = protoChildren
    .filter((it) => it != null)
    .map((it) => WindowContainer.childrenFromProto(it, isActivityInTree, nextSeq))
    .filter((it) => it != null);

  const identifier: any = identifierOverride ?? proto.identifier;
  const name: string = nameOverride ?? identifier?.title ?? '';
  const token: string = tokenOverride?.toString(16) ?? identifier?.hashCode?.toString(16) ?? '';

  const config = createConfigurationContainer(proto.configurationContainer);
  const entry = new WindowContainer(
    name,
    token,
    proto.orientation,
    proto.surfaceControl?.layerId ?? 0,
    visibleOverride ?? proto.visible,
    config,
    children,
    containerOrder
  );

  addAttributes(entry, proto);
  return entry;
};

function addAttributes(entry: WindowContainer, proto: any) {
  entry.proto = proto;
  entry.kind = entry.constructor.name;
  entry.shortName = shortenName(entry.name);
}

type WindowContainerChildType =
  | DisplayContent
  | DisplayArea
  | Task
  | TaskFragment
  | Activity
  | WindowToken
  | WindowState
  | WindowContainer;

WindowContainer.childrenFromProto = (
  proto: any,
  isActivityInTree: boolean,
  nextSeq: () => number
): WindowContainerChildType => {
  return (
    DisplayContent.fromProto(proto.displayContent, isActivityInTree, nextSeq) ??
    DisplayArea.fromProto(proto.displayArea, isActivityInTree, nextSeq) ??
    Task.fromProto(proto.task, isActivityInTree, nextSeq) ??
    TaskFragment.fromProto(proto.taskFragment, isActivityInTree, nextSeq) ??
    Activity.fromProto(proto.activity, nextSeq) ??
    WindowToken.fromProto(proto.windowToken, isActivityInTree, nextSeq) ??
    WindowState.fromProto(proto.window, isActivityInTree, nextSeq) ??
    WindowContainer.fromProto(proto.windowContainer, nextSeq)
  );
};

function createConfigurationContainer(proto: any): ConfigurationContainer {
  const entry = ConfigurationContainer.Companion.from(
    createConfiguration(proto?.overrideConfiguration ?? null),
    createConfiguration(proto?.fullConfiguration ?? null),
    createConfiguration(proto?.mergedOverrideConfiguration ?? null)
  );

  entry.obj = entry;
  return entry;
}

function createConfiguration(proto: any): Configuration {
  if (proto == null) {
    return null;
  }
  let windowConfiguration = null;

  if (proto != null && proto.windowConfiguration != null) {
    windowConfiguration = createWindowConfiguration(proto.windowConfiguration);
  }

  return Configuration.Companion.from(
    windowConfiguration,
    proto?.densityDpi ?? 0,
    proto?.orientation ?? 0,
    proto?.screenHeightDp ?? 0,
    proto?.screenHeightDp ?? 0,
    proto?.smallestScreenWidthDp ?? 0,
    proto?.screenLayout ?? 0,
    proto?.uiMode ?? 0
  );
}

function createWindowConfiguration(proto: any): WindowConfiguration {
  return WindowConfiguration.Companion.from(
    toRect(proto.appBounds),
    toRect(proto.bounds),
    toRect(proto.maxBounds),
    proto.windowingMode,
    proto.activityType
  );
}

export {WindowContainer};
