/**
 * App.test.js - Testing suite for app frontend code. 
 * Run with `npm test` in project root dir
 */
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MockAdapter from 'axios-mock-adapter'

import 'leaflet/dist/leaflet.css';

import MyApp, { generatePipeline } from './App';
import './components/IdMode'
import { InvalidLocationPopup } from './components/PopupModals';

let mock;
// Wrap App in BrowserRouter to mimic what's in Index. Link components break otherwise
let APP = <BrowserRouter><MyApp/></BrowserRouter>

describe('CO2 Pipeline Routing Tool Tests', function () {
  // Make variables set in Setup available to each test scope
  let user;

  // Setup before each test
  beforeEach(() => {
    user = userEvent.setup();
    mock = new MockAdapter(axios)
  });

  // Teardown after each tests
  afterEach(() => {
    mock.restore();
  });

  it('Confirm diclaimer modal open/close', () => {
    render(APP);

    const undBtn = screen.getByRole('button', {name: "Understood"});
    user.click(undBtn)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument;
  });

  it('Define custom startMarkerIcon with correct URL and size', () => {
    const icon = new L.Icon({
      iconUrl: 'https://cdn-icons-png.flaticon.com/512/447/447031.png',
      iconSize: [30, 30],
    });
    expect(icon.options.iconUrl).toBe(
      'https://cdn-icons-png.flaticon.com/512/447/447031.png'
    );
    expect(icon.options.iconSize).toStrictEqual([30, 30]);
  });

  it('Render header, map, and major body components', () => {
    render(APP);
    expect(screen.queryByText(/Smart CO2 Transport-Routing Tool/i)).toBeTruthy();

    // Body components
    expect(screen.queryByText("Add End Location in WGS84")).toBeTruthy();
    expect(screen.queryByText(/start location in world/i)).toBeTruthy();

    // Method 1 of checking for existence 
    const mapContainer = screen.getByTestId("map-container");
    expect(mapContainer).toBeInTheDocument();

    // Method 2 of checking for existence 
    expect(screen.queryByTestId("map-container")).toBeTruthy(); // the map component
  });

  it('handles invalid start point and shows error popup', async () => {
    const lat = 21.31
    const lon = -157.93
    let url = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="+lat+"&lon="+lon;

    const mockData = {
      address: {
        state: 'Hawaii',
        country: 'United States',
      }
    }
    mock.onGet('url').reply(200, mockData );
    render(APP);

    const idModeBtn = screen.getByRole('button', {name: /identify route/i})
    user.click(idModeBtn)

    const pipeModeBtn = screen.getByRole('button', {name: /pipeline mode/i})
    user.click(pipeModeBtn)

    user.click(screen.getByRole('button', {name: /save start/i}))

    render(<InvalidLocationPopup invalidPoint={true}/>)
    await waitFor(() => {
      expect(
        screen.getByText(/in the usa/i)).toBeInTheDocument()
    })
  });

  it('Sends core data correctly', () => {
    const mockData = { }
    mock.onGet('/token').reply(200, mockData)

    render(APP)

    user.click(screen.getByRole('button', {name: /generate pipeline/i}))
  });

  it('Error message for incorrect core data', async () => {
    const mockData = { }
    mock.onGet('/token').reply(400, mockData)

    render(APP)

    user.click(screen.getByRole('button', {name: /generate pipeline/i}))

    await waitFor(() => {
      expect(
        screen.getByText(/invalid/i)).toBeInTheDocument()
    })
  });

  it('Error message for incorrect point data', async () => {
    let url = "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=0&lon=0"
    const mockData = { }
    mock.onGet(url).reply(400, mockData)

    render(APP)

    user.click(screen.getByRole('button', {name: "Save Start"}))

    await waitFor(() => {
      expect(
        screen.getByRole('button', {name: "Understood"})).toBeInTheDocument()
    })
  });

});
