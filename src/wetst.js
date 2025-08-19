/***
 * Testing script for all the React code 
 * Run the tests with 'npm test' in the project root dir
 */

import React from 'react';
import {render, screen, fireEvent} from '@testing-library/react';
import { DisclaimerPopup } from './components/PopupModals';

describe('Disclaimer Popup', () => {
    test ('appears / closes correctly', () => {
        render(<DisclaimerPopup/>);
        const disclaimerBtn = screen.getByText('Understood');
        fireEvent.click(disclaimerBtn);
        expect (screen.queryByText('Disclaimer').not.toBeInTheDocument());
    });
});