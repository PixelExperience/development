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
import { HierarchyTreeBuilder } from "test/unit/hierarchy_tree_builder";
import { PresenterInputMethodClients } from "./presenter_input_method_clients";
import { executePresenterInputMethodTests } from "viewers/common/presenter_input_method_test_utils";

describe("PresenterInputMethodClients", () => {
  describe("PresenterInputMethod tests:", () => {
    const selectedTree = new HierarchyTreeBuilder()
      .setId("entry").setStableId("entry").build();

    executePresenterInputMethodTests(
      selectedTree,
      "elapsed",
      [2, 1],
      true,
      PresenterInputMethodClients,
      TraceType.INPUT_METHOD_CLIENTS,
    );
  });
});