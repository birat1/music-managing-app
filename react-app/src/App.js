
import { Container } from 'react-bootstrap';

function App() {
  return (
    <Container>
      <h1>Welcome to your APP!</h1>
      <p> You should follow the brief to implement tow pages "src/pages/Album.js" and "src/pages/Album.js"</p>
      <h2> Some important points:</h2>
      <ul>
        <li> Do not install any further dependencies  </li>
        <li> When complete, a user should be able to visit the pages: "http://localhost:3000/" and "http://localhost/album/:id" </li>
        <li> Don't add any further pages; however, your pages should consist of multiple components - you are welcome to create as many components as you like.
          You will have to make updates to "src/App.js" and "src/index.js" to implement functionality</li>
        <li>Do not hard code API requests. Rather, you should update (if necessary) and import API from "src/constants.js". You should then make requests like this:
          <pre>
            <code>
              {`
fetch(\`\${API}albums\`) 
or 
fetch(\`\${API}albums/\${id}\`)
  `}
            </code>
          </pre>
        </li>
      </ul>
    </Container>
  );
}

export default App;
