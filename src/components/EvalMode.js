/**
 * Component that contains all of the logic for 'Evaluate Corridor' mode
 */

import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

/**
 * All the code for Evaluate Corridor mode contained in one React Component, for organization and clarity 
 * @param {function} evaluateCorridor - The main functionality of Evaluate Corridor mode
 * @param {function} handleMultipleChange - Handles uploading multiple files
 * @param {funciton} handleDownload - Handles user downloading the generated pdf report file
 * @returns {JSX.element} - All the JSX code for Evaluate Corridor mode
 */
export default function EvalMode ( {evaluateCorridor, handleMultipleChange, handleDownload} ){

  function handlePDFDownload() {
    handleDownload('.pdf');
  }
    return(
        <div>
            <h4> Upload Shapefiles</h4>
            <form id="eval-form" onSubmit={evaluateCorridor}>
                <div classname='input-form'>
                    <Form.Group controlId="formFileMultiple" className="mb-3">
                        <Form.Label>Select one or more files to contribute to the shapefile used for corridor evaluation</Form.Label>
                        <Form.Control type="file" multiple onChange={ handleMultipleChange }/>
                    </Form.Group>
                </div>
                <Button id="submit-btn" type="submit">Evaluate</Button>
            </form>
            <br></br>
            <p>
                <Button onClick={handlePDFDownload}>
                <i className="fas fa-download"/>
                Download Report
                </Button>
            </p>
            <br/>
        </div>
    )
}