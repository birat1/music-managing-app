import React from 'react';
import { Navbar, Container } from 'react-bootstrap';

function AppNavbar() {
  return (
    <Navbar bg='dark' variant='dark' expand='lg' className='border-bottom'>
      <Container fluid>
        <Navbar.Brand className='fw-bold'>MyMusicMaestro</Navbar.Brand>
        <Navbar.Toggle aria-controls='basic-navbar-nav' />
        <Navbar.Collapse id='basic-navbar-nav'>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default AppNavbar;