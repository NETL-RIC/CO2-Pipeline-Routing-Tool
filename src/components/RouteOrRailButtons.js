/**
 * Component that contains the 'Pipeline Mode' and 'Railway Mode' buttons
 */

import * as React from 'react';
import Stack from '@mui/material/Stack';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

/**
 * The two exclusive selection buttons controlling "Pipeline Mode" and "Railway Mode" as a submode of Id Mode
 * @param {function} setBtnGroupState - Sets the submode of Id to "route" or "rail" for Pipeline and Railway respectively
 * @param {string} btntext1 - Button string for "Pipeline Mode"
 * @param {string} btntext2 - Button string for "Railway Mode"
 * @param {string} toolMode - String for whether the tool's main currently selected mode is Id, for conditional rendering
 * @returns {JSX.element} React component code for the two buttons
 */
export default function RouteOrRailButtons( {setBtnGroupState, btntxt1, btntxt2, toolMode} ) {
  const [mode, setMode] = React.useState('route');


  const handleChange = (event, newMode) => {
    // to prevent de-selection, ensures one button is pressed at all times
    if (newMode !== null){
      if (newMode === 'rail'){
        setBtnGroupState('rail')
      } else if (newMode === 'route'){
        setBtnGroupState('route')
      }
      setMode(newMode)
    }
  };

  const children = [
    <ToggleButton value="route" key="route">
      {btntxt1}
    </ToggleButton>,
    <ToggleButton value="rail" key="rail">
      {btntxt2}
    </ToggleButton>,
  ];

  const control = {
    value: mode,
    onChange: handleChange,
    exclusive: true,
  };

  return (
    <Stack spacing={2} 
      sx={{ 
        alignItems: 'left', 
        paddingLeft: '10px',
        paddingBottom: '10px',
      }}
    >
      <ToggleButtonGroup color='secondary' size="small" {...control} aria-label="IdModeButtons" disabled={toolMode !== 'id'}>
        {children}
      </ToggleButtonGroup>
    </Stack>
  );
}