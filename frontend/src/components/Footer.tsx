import React from "react";
const Footer: React.FC = () => {
  return (
    <>
      <footer className="footer">
        <p>
          Contribute to this project on{" "}
          <a
            target="_blank"
            href="https://github.com/metakgp/wimp"
            className="text-white"
          >
            <strong>GitHub </strong>
          </a>
          | Powered by{" "}
          <strong>
            <a
              target="_blank"
              href="https://metakgp.github.io/"
              className="text-white"
            >
              <strong> MetaKGP </strong>
            </a>
          </strong>
          with ❤️
        </p>
      </footer>
    </>
  );
};
export default Footer;
