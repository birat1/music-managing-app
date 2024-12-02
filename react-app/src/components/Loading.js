import React from 'react';
import { Spinner, Container, Col, Row } from 'react-bootstrap';

function Loading() {
  return (
    <Container fluid className="vh-100 d-flex justify-content-center align-items-center">
        <Row>
            <Col className="text-center">
                <Spinner animation="border" role="status">
                </Spinner>
                <p>Loading...</p>
            </Col>
        </Row>
    </Container>
  );
}

export default Loading;