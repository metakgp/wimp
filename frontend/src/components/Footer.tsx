import React from "react";
import "./footer.css";

const Footer: React.FC = () => {
  return (
    <footer>
      <p className="footer-text">
        Contribute to this project on{" "}
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://github.com/metakgp/wimp"
          className="text-white"
        >
          <strong>GitHub </strong>
        </a>
        | Powered by{" "}
        <strong>
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://metakgp.github.io/"
            className="text-white"
          >
            <strong> MetaKGP </strong>
          </a>
        </strong>
        with ❤️
      </p>
    </footer>
  );
};

export default Footer;
