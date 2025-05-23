
/**
 * All the components for all the different modal popups
 */

import {React, useState, useEffect} from 'react';
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

// Local Assets
import netlLogo from "../media/NETL_Square_GREEN_E.png";
import doeLogo from "../media/DOE_Logo_Color.png";
import discoverLogo from "../media/discover.jpg";

/**
 * Initial disclaimer popup that renders when the page is first loaded
 * @returns {JSX.element} React component code for the disclaimer message, containing the button to accept and close the modal
 */
export function DisclaimerPopup() {
    const [showDisclaimer, setShowDisclaimer] = useState(false);
    const handleClose = () => setShowDisclaimer(false);

    // useEffect with an empty dependency list means this will just run once on the inital render
    useEffect(() => {
        setShowDisclaimer(true);
    }, []);

    return (
      <>
        <Modal
          dialogClassName="dis-modal"
          show={showDisclaimer}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
        >
          <Modal.Header>
            <Modal.Title></Modal.Title>
            <div style={{ margin: "auto" }}>
              <img src={netlLogo} width={50} height={50} alt="NETL Logo" />
              <img src={doeLogo} height={50} alt="DOE Logo" />
              <img
                src={discoverLogo}
                width={120}
                height={50}
                alt="Discover Logo"
              />
            </div>
          </Modal.Header>
          <div id="disTitle" className="modal-body">
            <label id="disTitleText">Disclaimer</label>
          </div>
          <Modal.Body>
            This project was funded by the United States Department of Energy,
            National Energy Technology Laboratory, in part, through a site
            support contract. Neither the United States Government nor any
            agency thereof, nor any of their employees, nor the support
            contractor, nor any of their employees, makes any warranty, express
            or implied, or assumes any legal liability or responsibility for the
            accuracy, completeness, or usefulness of any information, apparatus,
            product, or process disclosed, or represents that its use would not
            infringe privately owned rights. Reference herein to any specific
            commercial product, process, or service by trade name, trademark,
            manufacturer, or otherwise does not necessarily constitute or imply
            its endorsement, recommendation, or favoring by the United States
            Government or any agency thereof. The views and opinions of authors
            expressed herein do not necessarily state or reflect those of the
            United States Government or any agency thereof. Parts of this
            technical effort were performed in support of the National Energy
            Technology Laboratory's ongoing research under the Energy Data
            eXchange for Carbon Capture and Storage (EDX4CCS) Field Work
            Proposal 1025007 by NETL's Research and Innovation Center, including
            work performed by Leidos Research Support Team staff under the RSS
            contract 326663.00.0.2.00.00.2050.033.0.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }

  /**
   * Loading message modal that appears when Id Mode is doing its calculations. 
   * Will block interaction with the rest of the tool while present
   * @param {boolean} isLoadingIdMode - Controls whether the loading modal for Id Mode is displayed
   * @returns {JSX.element} Component code for the loading message
   */
  export function LoadingMessageIdMode( {isLoadingIdMode} ) {
    if (isLoadingIdMode) {
      return (
        <>
          <Modal
            show={isLoadingIdMode}
            backdrop="static"
            keyboard={false}
            aria-labelledby="contained-modal-title-vcenter"
            centered
          >
            <Modal.Header>
              <Modal.Title>Loading...</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Optimizing pipeline corridor, this may take several minutes.
              Please do not close the webpage, or your progress will be lost.
            </Modal.Body>
            <Modal.Footer>
              This notification will close automatically when optimization has
              concluded.
            </Modal.Footer>
          </Modal>
        </>
      );
    }
  }

  /**
   * Loading message modal that appears when Eval Mode is doing its calculations. 
   * Will block interaction with the rest of the tool while present
   * @param {boolean} isLoadingEvalMode - Controls whether the loading modal for Eval Mode is displayed
   * @returns {JSX.element} Component code for the loading message
   */
  export function LoadingMessageEvalMode({isLoadingEvalMode}) {
    if (isLoadingEvalMode) {
      return (
        <>
          <Modal
            show={isLoadingEvalMode}
            backdrop="static"
            keyboard={false}
            aria-labelledby="contained-modal-title-vcenter"
            centered
          >
            <Modal.Header>
              <Modal.Title>Loading...</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              Evaluating uploaded corridor, this may take several minutes.
              Please do not close the webpage, or your progress will be lost.
            </Modal.Body>
            <Modal.Footer>
              This notification will close automatically when evaluation has
              concluded.
            </Modal.Footer>
          </Modal>
        </>
      );
    }
  }

  /**
   * Catch-all for invalid points, bad logic, etc, anything that stops the server.
   * @param {boolean} showServerError - Controls whether the server error modal appears or not.
   * @param {function} setShowServerError - Setter for showServerError
   * @returns {JSX.elements} Component code for the error message modal
   */
  export function ServerErrorPopup({showServerError, setShowServerError}) {
    const handleClose = () => setShowServerError(false);
    return (
      <>
        <Modal
          show={showServerError}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header>
            <Modal.Title>Server Error</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            An invalid point location may have been selected, the server may not
            have been started, or a different server error has occured.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }

  /**
   * Modal displaying error message for invalid location
   * @param {boolean} invalidPoint - Boolean indicating the most recently selected point is outside the US or Alaska
   * @param {function} setInvalidPoint - Setter for invalidPoint
   * @returns {JSX.element} - Modal component code for Invalid Location popup, contains button to dismiss
   */
  export function InvalidLocationPopup({invalidPoint, setInvalidPoint}) {
    const handleClose = () => setInvalidPoint(false);
    return (
      <>
        <Modal
          show={invalidPoint}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header>
            <Modal.Title>Invalid Location</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Please select a point within the USA or Alaska.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }

  /**
   * Modal displaying error message when the two points are in seperate landmasses (mainland USA vs Alaska)
   * @param {boolean} invalidLandmass - Set to true when both points aren't in the same landmass
   * @param {function} setInvalidLandmass - Setter for invalidLandmass
   * @returns {JSX.element} - Modal component code for Invalid Pipeline popup, contains button to dismiss
   */
  export function InvalidLandmassPopup({invalidLandmass, setInvalidLandmass}) {
    const handleClose = () => setInvalidLandmass(false)
    return (
      <>
        <Modal
          show={invalidLandmass}
          onHide={handleClose}
          backdrop="static"
          keyboard={false}
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header>
            <Modal.Title>Invalid Pipeline</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Start and end locations must be both in Alaska or both in
            continental USA.
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={handleClose}>Understood</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }
