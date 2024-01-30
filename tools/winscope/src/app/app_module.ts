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

import {DragDropModule} from '@angular/cdk/drag-drop';
import {ScrollingModule} from '@angular/cdk/scrolling';
import {CommonModule} from '@angular/common';
import {HttpClientModule} from '@angular/common/http';
import {CUSTOM_ELEMENTS_SCHEMA, NgModule} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatDividerModule} from '@angular/material/divider';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatGridListModule} from '@angular/material/grid-list';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatListModule} from '@angular/material/list';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatRadioModule} from '@angular/material/radio';
import {MatSelectModule} from '@angular/material/select';
import {MatSliderModule} from '@angular/material/slider';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTabsModule} from '@angular/material/tabs';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatTooltipModule} from '@angular/material/tooltip';
import {BrowserModule} from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {CoordinatesTableComponent} from 'viewers/components/coordinates_table_component';
import {HierarchyComponent} from 'viewers/components/hierarchy_component';
import {ImeAdditionalPropertiesComponent} from 'viewers/components/ime_additional_properties_component';
import {PropertiesComponent} from 'viewers/components/properties_component';
import {PropertiesTableComponent} from 'viewers/components/properties_table_component';
import {PropertyGroupsComponent} from 'viewers/components/property_groups_component';
import {RectsComponent} from 'viewers/components/rects/rects_component';
import {TransformMatrixComponent} from 'viewers/components/transform_matrix_component';
import {TreeComponent} from 'viewers/components/tree_component';
import {TreeNodeComponent} from 'viewers/components/tree_node_component';
import {TreeNodeDataViewComponent} from 'viewers/components/tree_node_data_view_component';
import {TreeNodePropertiesDataViewComponent} from 'viewers/components/tree_node_properties_data_view_component';
import {ViewerInputMethodComponent} from 'viewers/components/viewer_input_method_component';
import {ViewerProtologComponent} from 'viewers/viewer_protolog/viewer_protolog_component';
import {ViewerScreenRecordingComponent} from 'viewers/viewer_screen_recording/viewer_screen_recording_component';
import {ViewerSurfaceFlingerComponent} from 'viewers/viewer_surface_flinger/viewer_surface_flinger_component';
import {ViewerTransactionsComponent} from 'viewers/viewer_transactions/viewer_transactions_component';
import {ViewerTransitionsComponent} from 'viewers/viewer_transitions/viewer_transitions_component';
import {ViewerViewCaptureComponent} from 'viewers/viewer_view_capture/viewer_view_capture_component';
import {ViewerWindowManagerComponent} from 'viewers/viewer_window_manager/viewer_window_manager_component';
import {AdbProxyComponent} from './components/adb_proxy_component';
import {AppComponent} from './components/app_component';
import {
  MatDrawer,
  MatDrawerContainer,
  MatDrawerContent,
} from './components/bottomnav/bottom_drawer_component';
import {CollectTracesComponent} from './components/collect_traces_component';
import {LoadProgressComponent} from './components/load_progress_component';
import {SnackBarComponent} from './components/snack_bar_component';
import {ExpandedTimelineComponent} from './components/timeline/expanded_timeline_component';
import {MiniTimelineComponent} from './components/timeline/mini_timeline_component';
import {SingleTimelineComponent} from './components/timeline/single_timeline_component';
import {TimelineComponent} from './components/timeline/timeline_component';
import {TraceConfigComponent} from './components/trace_config_component';
import {TraceViewComponent} from './components/trace_view_component';
import {UploadTracesComponent} from './components/upload_traces_component';
import {WebAdbComponent} from './components/web_adb_component';

@NgModule({
  declarations: [
    AppComponent,
    ViewerWindowManagerComponent,
    ViewerSurfaceFlingerComponent,
    ViewerInputMethodComponent,
    ViewerProtologComponent,
    ViewerTransactionsComponent,
    ViewerScreenRecordingComponent,
    ViewerTransitionsComponent,
    ViewerViewCaptureComponent,
    CollectTracesComponent,
    UploadTracesComponent,
    AdbProxyComponent,
    WebAdbComponent,
    TraceConfigComponent,
    HierarchyComponent,
    PropertiesComponent,
    RectsComponent,
    TraceViewComponent,
    TreeComponent,
    TreeNodeComponent,
    TreeNodeDataViewComponent,
    TreeNodePropertiesDataViewComponent,
    PropertyGroupsComponent,
    TransformMatrixComponent,
    PropertiesTableComponent,
    ImeAdditionalPropertiesComponent,
    CoordinatesTableComponent,
    TimelineComponent,
    MiniTimelineComponent,
    ExpandedTimelineComponent,
    SingleTimelineComponent,
    SnackBarComponent,
    MatDrawer,
    MatDrawerContent,
    MatDrawerContainer,
    LoadProgressComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatGridListModule,
    FormsModule,
    MatListModule,
    MatCheckboxModule,
    MatDividerModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatSliderModule,
    MatRadioModule,
    MatTooltipModule,
    MatToolbarModule,
    MatTabsModule,
    MatSnackBarModule,
    ScrollingModule,
    DragDropModule,
    ReactiveFormsModule,
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  bootstrap: [AppComponent],
})
export class AppModule {}
