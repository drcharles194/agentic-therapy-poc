export enum ViewMode {
  USER = 'user',
  THERAPIST = 'therapist'
}
 
export interface ViewState {
  currentView: ViewMode;
  switchView: () => void;
} 