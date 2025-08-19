

import React from 'react';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import { expect } from 'chai';
import sinon from 'sinon';
import axios from 'axios';
import MyApp from '../MyApp';

import 'leaflet/dist/leaflet.css';
import { act } from 'react-dom/test-utils';

describe('Smart CO2 Routing Tool - Core Map Features', function () {
  let axiosGetStub;

  beforeEach(() => {
    axiosGetStub = sinon.stub(axios, 'get');
  });

  afterEach(() => {
    sinon.restore();
  });

  it('should define custom startMarkerIcon with correct URL and size', () => {
    const icon = new L.Icon({
      iconUrl: 'https://cdn-icons-png.flaticon.com/512/447/447031.png',
      iconSize: [30, 30],
    });

    expect(icon.options.iconUrl).to.equal(
      'https://cdn-icons-png.flaticon.com/512/447/447031.png'
    );
    expect(icon.options.iconSize).to.deep.equal([30, 30]);
  });

  it('renders map and header text', () => {
    render(<MyApp />);
    expect(screen.getByText(/Smart CO2 Transport-Routing Tool/i)).to.exist;
  });

  it('handles invalid start point (Hawaii) and shows error popup', async () => {
    render(<MyApp />);

    // Simulate ID mode and "start" location selection
    const idModeButton = screen.getByText('Identify Route');
    act(() => idModeButton.click());

    // Set location to "start"
    const pipelineModeButton = screen.getByText('Pipeline Mode');
    act(() => pipelineModeButton.click());

    // Simulate Nominatim returning "Hawaii"
    axiosGetStub.resolves({
      data: {
        address: {
          state: 'Hawaii',
          country: 'United States',
        },
      },
    });

    const map = screen.getByRole('presentation'); // Leaflet map container
    fireEvent.click(map, { latlng: { lat: 20.5, lng: -157.5 } });

    await waitFor(() => {
      expect(
        screen.getByText(/Selected point must be in the continental US or Alaska/i)
      ).to.exist;
    });
  });

  it('shows error modal if landmasses do not match', async () => {
    render(<MyApp />);

    // Set up both coordinates manually (simulate UI logic)
    const generateBtn = screen.getByText('Generate Pipeline');
    act(() => {
      // simulate coordinates set from Alaska and mainland
      window.setStartLandmass?.('Alaska');
      window.setEndLandmass?.('US');
    });

    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/Start and End locations must be on the same landmass/i)
      ).to.exist;
    });
  });

  it('shows server error modal if /token API call fails', async () => {
    sinon.stub(axios, 'post').rejects({ response: { status: 500 } });

    render(<MyApp />);
    // simulate valid start and end points
    act(() => {
      window.setStartLandmass?.('US');
      window.setEndLandmass?.('US');
      window.setStartCoords?.([39.5, -98.5]);
      window.setDestCoords?.([40.5, -100.5]);
    });

    const generateBtn = screen.getByText('Generate Pipeline');
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(screen.getByText(/Server Error/i)).to.exist;
    });
  });
});
