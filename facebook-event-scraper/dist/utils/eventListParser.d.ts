import { ShortEventData } from '../types';
import { EventType } from '../enums';
export declare const getEventListFromPageOrProfile: (html: string) => Pick<ShortEventData, 'id' | 'name' | 'url' | 'date' | 'isCanceled' | 'isPast'>[];
export declare const getEventListFromGroup: (html: string, type?: EventType) => Pick<ShortEventData, 'id' | 'name' | 'url' | 'date' | 'isCanceled' | 'isPast'>[];
