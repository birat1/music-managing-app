import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Container, Row, Col, Image, ListGroup } from 'react-bootstrap';
import { API } from '../constants';

const fetchAlbum = async ({ queryKey }) => {
  const [, id] = queryKey;
  const response = await fetch(`${API}albums/${id}`);
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
};

function Album() {
  const { id } = useParams();
  const { data: album, error, isLoading } = useQuery({
    queryKey: ['album', id],
    queryFn: fetchAlbum,
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading album: {error.message}</div>;

  const totalMinutes = Math.floor(album.total_playtime / 60);
  const totalSeconds = album.total_playtime % 60;

  return (
    <Container className='mt-4'>
      <Row>
        <Col md={4}>
          <Image src={album.cover_image} alt={album.title} fluid />
          <ListGroup className='tracklist mt-3 border-0'>
            {album.tracks.map((track, index) => (
              <ListGroup.Item key={track.id} className='track-item border-0'>
                {index + 1}. {track.title}
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Col>
        <Col md={8}>
          <h1 className='fw-bold'>{album.title}</h1>
          <h4 className='fw-bold'>£{album.price}</h4>
          <p>
            {album.artist} ({album.release_year}), {album.tracks.length} Songs, {totalMinutes} min {totalSeconds} sec
          </p>
          <p className='text-muted'>{album.description}</p>
        </Col>
      </Row>
    </Container>
  );
}

export default Album;