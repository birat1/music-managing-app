import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { API } from '../constants';
import { Card, Row, Col, Container } from 'react-bootstrap';
import './Home.css';
import Error from '../components/Error';
import Loading from '../components/Loading';

const fetchAlbums = async () => {
    const response = await fetch(`${API}albums/`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  };
  
function Home() {
    const { data: albums, error, isLoading } = useQuery({
        queryKey: ['albums'],
        queryFn: fetchAlbums,
    });

    if (isLoading) return <Loading />;
    if (error) return <Error message={`Error loading album: ${error.message}`} />;

    return (
        <Container className='mt-4'>
        <Row className='g-5'>
            {albums.map(album => (
            <Col key={album.id} sm={12} md={6} lg={4}>
                <Card className='mb-4 album-card'>
                <Card.Img variant='top' src={album.cover_image} className='album-cover' />
                <Card.Body>
                    <Card.Title className='album-title fw-bold'>
                    <a href={`/albums/${album.id}`}>
                        {album.title}
                    </a>
                    </Card.Title>
                    <Card.Text>
                    <span className='album-price fw-bold'>£{album.price}</span><br />
                    <span className='d-block mb-2'>{album.artist} ({album.release_year})</span>
                    <span className='text-muted'>{album.short_description}</span>
                    </Card.Text>
                </Card.Body>
                </Card>
            </Col>
            ))}
        </Row>
        </Container>
    );
}
  
  export default Home;